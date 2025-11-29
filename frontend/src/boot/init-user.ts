// src/boot/init-user.ts
import { boot } from 'quasar/wrappers'
import { useUserStore } from 'stores/userStore'

export default boot(async () => {
  const userStore = useUserStore()

  try {
    userStore.loadDataFromLocalStorage();
    await userStore.setMyCurrentLeagueId();
  } catch (err) {
    console.error('Failed to load user on boot:', err)
  }
})
