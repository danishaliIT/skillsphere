from rest_framework import serializers
from .models import (
    StudentProfile,
    InstructorProfile,
    CompanyProfile,
    StudentAddress,
    StudentEducation,
    StudentSocial,
)

from .models import (
    InstructorEducation,
    InstructorEmployment,
    InstructorCertificate,
)


class StudentAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAddress
        fields = '__all__'


class StudentEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEducation
        fields = '__all__'


class StudentSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSocial
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    address = StudentAddressSerializer(read_only=True)
    education_history = StudentEducationSerializer(many=True, read_only=True)
    socials = StudentSocialSerializer(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = StudentProfile
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'bio',
            'phone_number',
            'experience',
            'public_profile',
            'profile_picture',
            'address',
            'education_history',
            'socials',
        ]


class InstructorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    # Nested serializers for related data
    education = serializers.SerializerMethodField()
    employment = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    socials = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = [
            'full_name',
            'expertise',
            'experience_years',
            'bio',
            'rating',
            'profile_picture',
            'phone_number',
            'linkedin',
            'website',
            'skills',
            'public_profile',
            'bank_name',
            'bank_account_number',
            'bank_iban',
            'bank_swift',
            'education',
            'employment',
            'certificates',
            'socials',
            'address',
            'email',
            'username',
        ]

    def get_education(self, obj):
        from .models import InstructorEducation
        return [
            {
                'id': e.id,
                'institution': e.institution,
                'degree': e.degree,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'grade': e.grade,
            }
            for e in InstructorEducation.objects.filter(profile=obj)
        ]

    def get_employment(self, obj):
        from .models import InstructorEmployment
        return [
            {
                'id': ex.id,
                'company': ex.company,
                'title': ex.title,
                'start_date': ex.start_date,
                'end_date': ex.end_date,
                'description': ex.description,
            }
            for ex in InstructorEmployment.objects.filter(profile=obj)
        ]

    def get_certificates(self, obj):
        from .models import InstructorCertificate
        return [
            {
                'id': c.id,
                'title': c.title,
                'issuer': c.issuer,
                'issued_date': c.issued_date,
                'file': c.file.url if c.file else None,
            }
            for c in InstructorCertificate.objects.filter(profile=obj)
        ]

    def get_socials(self, obj):
        try:
            s = obj.socials
            return {
                'linkedin': s.linkedin,
                'twitter': s.twitter,
                'github': s.github,
                'website': s.website,
            }
        except Exception:
            return {}

    def get_address(self, obj):
        try:
            a = obj.address
            return {
                'street_address': a.street_address,
                'city': a.city,
                'state': a.state,
                'country': a.country,
                'zip_code': a.zip_code,
            }
        except Exception:
            return {}


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'


class InstructorEducationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstructorEducation
        fields = ['id', 'profile', 'institution', 'degree', 'start_date', 'end_date', 'grade']
        read_only_fields = ['profile']


class InstructorEmploymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstructorEmployment
        fields = ['id', 'profile', 'company', 'title', 'start_date', 'end_date', 'description']
        read_only_fields = ['profile']


class InstructorCertificateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    file = serializers.FileField(allow_null=True, required=False)

    class Meta:
        model = InstructorCertificate
        fields = ['id', 'profile', 'title', 'issuer', 'issued_date', 'file']
        read_only_fields = ['profile']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file:
            try:
                data['file'] = instance.file.url
            except Exception:
                data['file'] = None
        else:
            data['file'] = None
        return data