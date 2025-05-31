from django_filters import rest_framework as filters
from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    type = filters.CharFilter(field_name='type')
    status = filters.CharFilter(field_name='status')
    color = filters.CharFilter(field_name='color')
    eye_color = filters.CharFilter(field_name='eye_color')
    face_shape = filters.CharFilter(field_name='face_shape')
    special_features = filters.CharFilter(field_name='special_features')
    breed = filters.CharFilter(field_name='breed', lookup_expr='icontains')
    created_at = filters.DateTimeFromToRangeFilter()
    latitude = filters.NumberFilter()
    longitude = filters.NumberFilter()
    radius = filters.NumberFilter(method='filter_by_radius')

    def filter_by_radius(self, queryset, name, value):
        """
        Filter advertisements within a radius (in kilometers) of a given point.
        Requires latitude and longitude parameters.
        """
        latitude = self.data.get('latitude')
        longitude = self.data.get('longitude')
        
        if not (latitude and longitude and value):
            return queryset

        # Haversine formula for calculating distance
        haversine_formula = """
            6371 * acos(
                cos(radians(%s)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(%s)) +
                sin(radians(%s)) * sin(radians(latitude))
            )
        """
        
        queryset = queryset.extra(
            select={'distance': haversine_formula % (latitude, longitude, latitude)},
            where=['6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude))) <= %s'],
            params=[latitude, longitude, latitude, value]
        )
        
        return queryset

    class Meta:
        model = Advertisement
        fields = [
            'type', 
            'status', 
            'color', 
            'eye_color', 
            'face_shape', 
            'special_features',
            'breed',
            'created_at', 
            'latitude', 
            'longitude'
        ]
