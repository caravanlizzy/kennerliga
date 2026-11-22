import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';

export interface UserProfileIdentity {
  profileId?: number | null;
  profile?: number | null;
  id?: number | null;
  username?: string | null;
  avatar_shape?: string | null;
  avatar_color?: string | null;
}

export function useUserProfileDisplay() {
  const userStore = useUserStore();
  const { user } = storeToRefs(userStore);

  function isCurrentUser(
    playerProfileId?: number | null,
    username?: string | null
  ): boolean {
    if (!user.value) return false;
    if (
      playerProfileId !== undefined &&
      playerProfileId !== null &&
      user.value.profile_id === playerProfileId
    ) {
      return true;
    }
    if (username && user.value.username === username) {
      return true;
    }
    return false;
  }

  function resolveAvatarShape(
    playerProfileId?: number | null,
    username?: string | null,
    fallbackShape?: string | null
  ): string | undefined {
    if (isCurrentUser(playerProfileId, username) && user.value?.avatar_shape) {
      return user.value.avatar_shape;
    }
    return fallbackShape || undefined;
  }

  function resolveAvatarColor(
    playerProfileId?: number | null,
    username?: string | null,
    fallbackColor?: string | null
  ): string | undefined {
    if (
      isCurrentUser(playerProfileId, username) &&
      user.value?.avatar_color !== undefined &&
      user.value?.avatar_color !== null
    ) {
      return user.value.avatar_color;
    }
    return fallbackColor || undefined;
  }

  function formatPlayerLabel(profileName?: string | null, username?: string | null): string {
    if (!profileName && !username) return '';
    if (!username || username === profileName) {
      return profileName || username || '';
    }
    return `${profileName} (@${username})`;
  }

  function formatPoints(pts: number | string | undefined | null): string {
    if (pts === undefined || pts === null) return '0';
    const num = Number(pts);
    if (isNaN(num)) return '0';
    return num % 1 === 0 ? num.toFixed(0) : num.toFixed(2);
  }

  return {
    currentUser: user,
    isCurrentUser,
    resolveAvatarShape,
    resolveAvatarColor,
    formatPlayerLabel,
    formatPoints,
  };
}
