// src/boot/init-user.ts
import { boot } from 'quasar/wrappers'
import { useUserStore } from 'stores/userStore'

export default boot(async () => {
  const userStore = useUserStore()

  try {
    // Session state is restored by `pinia-plugin-persistedstate` when the
    // store is first instantiated (see its `afterRestore` hook), so we only
    // need to refresh the league the user is currently playing in.
    await userStore.setMyCurrentLeagueId();
  } catch (err) {
    console.error('Failed to load user on boot:', err)
  }
})
