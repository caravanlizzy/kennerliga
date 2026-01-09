from rest_framework import serializers
from game.models import ResultConfig, Faction
from .models import Result


class ResultSerializer(serializers.ModelSerializer):
    faction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    factions = serializers.SerializerMethodField(read_only=True)
    player_profile_name = serializers.SerializerMethodField(read_only=True)
    decisive_tie_breaker = serializers.SerializerMethodField(required=False, read_only=True)
    game_name = serializers.CharField(source='selected_game.game.name', read_only=True)

    class Meta:
        model = Result
        fields = [
            'id',
            'player_profile',
            'player_profile_name',
            'selected_game',
            'game_name',
            'points',
            'starting_points',
            'starting_position',
            'position',
            'notes',
            'tie_breaker_value',
            'decisive_tie_breaker',
            'faction_ids',
            'factions',
        ]

    def get_factions(self, obj):
        return [
            {
                "id": f.id,
                "name": f.name,
                "level": f.level
            } for f in obj.factions.all()
        ]

    def get_player_profile_name(self, obj):
        return obj.player_profile.profile_name

    def get_decisive_tie_breaker(self, obj):
        if isinstance(obj, dict):
            # This is a dict, skip processing (likely in dry_run)
            return obj.get("decisive_tie_breaker")

        if hasattr(obj, 'decisive_tie_breaker') and obj.decisive_tie_breaker:
            return {
                "id": obj.decisive_tie_breaker.id,
                "name": obj.decisive_tie_breaker.name
            }
        return None

    def validate(self, data):
        selected_game = data.get('selected_game')
        if not selected_game:
            raise serializers.ValidationError("SelectedGame is required.")

        result_config = ResultConfig.objects.filter(game=selected_game.game).first()
        if not result_config:
            raise serializers.ValidationError("ResultConfig is missing for this game.")

        # ✅ Validate faction requirement
        if result_config.is_asymmetric:
            if 'faction_ids' not in self.initial_data or not self.initial_data['faction_ids']:
                raise serializers.ValidationError("At least one faction is required for asymmetric games.")

        # ✅ Validate starting points system
        if result_config.starting_points_system and result_config.starting_points_system.code == "DYNAMIC":
            if 'starting_points' not in data or data['starting_points'] is None:
                raise serializers.ValidationError("Starting points are required when the system is DYNAMIC.")

        # ✅ Validate starting position requirement
        if not result_config.has_starting_player_order:
            data['starting_position'] = None  # ignore if not needed
        elif 'starting_position' not in data:
            raise serializers.ValidationError("Starting position is required.")

        # ✅ Validate points requirement
        if result_config.has_points:
            if 'points' not in data:
                raise serializers.ValidationError("Points are required for this game.")

        return data

    def create(self, validated_data):
        selected_game = validated_data['selected_game']
        faction_ids = validated_data.pop('faction_ids', [])

        # Auto-fill league and season
        validated_data['league'] = selected_game.league
        validated_data['season'] = selected_game.league.season

        instance = super().create(validated_data)

        # Set factions (Many-to-Many)
        if faction_ids:
            factions = Faction.objects.filter(id__in=faction_ids)
            instance.factions.set(factions)

    def update(self, instance, validated_data):
        faction_ids = validated_data.pop('faction_ids', None)
        instance = super().update(instance, validated_data)

        if faction_ids is not None:
            factions = Faction.objects.filter(id__in=faction_ids)
            instance.factions.set(factions)

        return instance
