# -*- coding: utf-8 -*-
"""
Entities serializer module.
"""
from django.utils.translation import gettext as _

from pyxform.constants import ENTITIES_RESERVED_PREFIX

from rest_framework import serializers
from rest_framework.reverse import reverse

from onadata.apps.logger.models import (
    Entity,
    EntityList,
    FollowUpForm,
    Project,
    RegistrationForm,
    XForm,
)
from onadata.apps.logger.tasks import delete_entities_bulk_async
from onadata.libs.permissions import CAN_VIEW_PROJECT


class EntityListSerializer(serializers.ModelSerializer):
    """Default Serializer for EntityList"""

    def validate_name(self, value: str) -> str:
        """Validate `name` field

        Uses the same validation rules as PyXForm rules for dataset name
        """
        if value.startswith(ENTITIES_RESERVED_PREFIX):
            err_msg = f"May not start with reserved prefix {ENTITIES_RESERVED_PREFIX}."
            raise serializers.ValidationError(_(err_msg))

        if "." in value:
            raise serializers.ValidationError("May not include periods.")

        return value

    def validate_project(self, value: Project) -> Project:
        """Validate `project` field"""
        user = self.context["request"].user

        if not value.shared and not user.has_perm(CAN_VIEW_PROJECT, value):
            raise serializers.ValidationError(
                f'Invalid pk "{value.pk}" - object does not exist.',
                code="does_not_exist",
            )

        return value

    class Meta:
        model = EntityList
        fields = (
            "id",
            "name",
            "project",
            "date_created",
            "date_modified",
        )
        read_only_fields = (
            "date_created",
            "date_modified",
        )


class EntityListArraySerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for an array of EntityList"""

    url = serializers.HyperlinkedIdentityField(
        view_name="entity_list-detail", lookup_field="pk"
    )
    project = serializers.HyperlinkedRelatedField(
        view_name="project-detail",
        lookup_field="pk",
        queryset=Project.objects.all(),
    )
    public = serializers.BooleanField(source="project.shared")
    num_registration_forms = serializers.SerializerMethodField()
    num_follow_up_forms = serializers.SerializerMethodField()

    def get_num_registration_forms(self, obj: EntityList) -> int:
        """Returns number of RegistrationForms for EntityList object"""
        return obj.registration_forms.count()

    def get_num_follow_up_forms(self, obj: EntityList) -> int:
        """Returns number of FollowUpForms consuming Entities from dataset"""
        return obj.follow_up_forms.count()

    class Meta:
        model = EntityList
        fields = (
            "url",
            "id",
            "name",
            "project",
            "public",
            "date_created",
            "date_modified",
            "num_registration_forms",
            "num_follow_up_forms",
            "num_entities",
        )


class RegistrationFormInlineSerializer(serializers.HyperlinkedModelSerializer):
    """Inline serializer for RegistrationForm"""

    title = serializers.CharField(source="xform.title")
    xform = serializers.HyperlinkedRelatedField(
        view_name="xform-detail",
        lookup_field="pk",
        queryset=XForm.objects.all(),
    )
    id_string = serializers.CharField(source="xform.id_string")
    save_to = serializers.SerializerMethodField()

    def get_save_to(self, obj: RegistrationForm) -> list[str]:
        """Returns the save_to fields defined in the XLSForm"""
        return list(obj.get_save_to().keys())

    class Meta:
        model = RegistrationForm
        fields = (
            "title",
            "xform",
            "id_string",
            "save_to",
        )


class FollowUpFormInlineSerializer(serializers.HyperlinkedModelSerializer):
    """Inline serializer for FollowUpForm"""

    title = serializers.CharField(source="xform.title")
    xform = serializers.HyperlinkedRelatedField(
        view_name="xform-detail",
        lookup_field="pk",
        queryset=XForm.objects.all(),
    )
    id_string = serializers.CharField(source="xform.id_string")

    class Meta:
        model = FollowUpForm
        fields = (
            "title",
            "xform",
            "id_string",
        )


class EntityListDetailSerializer(EntityListArraySerializer):
    """Serializer for EntityList detail"""

    registration_forms = RegistrationFormInlineSerializer(many=True, read_only=True)
    follow_up_forms = FollowUpFormInlineSerializer(many=True, read_only=True)

    class Meta:
        model = EntityList
        fields = (
            "id",
            "name",
            "project",
            "public",
            "date_created",
            "date_modified",
            "num_registration_forms",
            "num_follow_up_forms",
            "num_entities",
            "registration_forms",
            "follow_up_forms",
        )


class EntitySerializer(serializers.ModelSerializer):
    """Serializer for Entity"""

    label = serializers.CharField(write_only=True, required=False)
    data = serializers.JSONField(write_only=True, required=False)

    def validate_data(self, value):
        """Validates Entity dataset properties"""
        if value:
            for key in value.keys():
                if key not in self.context["entity_list"].properties:
                    raise serializers.ValidationError(
                        _(f"Invalid dataset property {key}.")
                    )

        return value

    def update(self, instance, validated_data):
        data = validated_data.pop("data", {})
        label = validated_data.pop("label", None)

        if label:
            instance.json["label"] = label

        if data:
            updated_data = {**instance.json, **data}

            for key, value in data.items():
                if not value:
                    # Unset property
                    del updated_data[key]

            instance.json = updated_data

        instance.save()
        instance.history.create(
            json=instance.json, created_by=self.context["request"].user
        )

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        instance_json = data.pop("json")

        return {**data, "data": instance_json}

    class Meta:
        model = Entity
        fields = (
            "id",
            "uuid",
            "date_created",
            "date_modified",
            "json",
            "label",
            "data",
        )


class EntityArraySerializer(EntitySerializer):
    """Serializer for a list of Entities"""

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        """Returns the URL to an Entity list."""
        entity_list = self.context["entity_list"]
        request = self.context["request"]
        response_format = self.context.get("format")
        kwargs = {"pk": entity_list.pk, "entity_pk": obj.pk}

        return reverse(
            "entity_list-entities",
            kwargs=kwargs,
            request=request,
            format=response_format,
        )

    class Meta:
        model = Entity
        fields = (
            "url",
            "id",
            "uuid",
            "date_created",
            "json",
            "label",
            "data",
        )


# pylint: disable=abstract-method
class EntityDeleteSerializer(serializers.Serializer):
    """Serializer for deleting Entities"""

    entity_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_entity_ids(self, ids):
        entities = Entity.objects.filter(
            pk__in=ids, deleted_at__isnull=True, entity_list=self.context["entity_list"]
        )

        if entities.count() != len(ids):
            raise serializers.ValidationError(
                "One or more entities does not exist.", code="does_not_exist"
            )

        return ids

    def save(self, **kwargs):
        entity_ids = self.validated_data["entity_ids"]

        delete_entities_bulk_async.delay(
            entity_ids, self.context["request"].user.username
        )
