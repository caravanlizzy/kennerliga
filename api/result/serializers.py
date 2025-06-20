from rest_framework import serializers
from game.models import SelectedGame, ResultConfig, Faction, TieBreaker
from .models import Result


class ResultSerializer(serializers.ModelSerializer):
    faction_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    faction_name = serializers.SerializerMethodField(read_only=True)
    decisive_tie_breaker = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Result
        fields = [
            'id',
            'player_profile',
            'selected_game',
            'points',
            'starting_position',
            'tie_breaker_value',
            'decisive_tie_breaker',
            'faction_id',
            'faction_name',
        ]

    def get_faction_name(self, obj):
        return obj.faction.name if getattr(obj, 'faction', None) else None

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
            if 'faction_id' not in self.initial_data:
                raise serializers.ValidationError("Faction is required for asymmetric games.")

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

        # Auto-fill league and season
        validated_data['league'] = selected_game.league
        validated_data['season'] = selected_game.league.season

        # Set faction if provided
        faction_id = self.initial_data.get('faction_id')
        if faction_id:
            validated_data['faction'] = Faction.objects.get(id=faction_id)

        return super().create(validated_data)
