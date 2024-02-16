import { useUserStore } from 'stores/userStore';


export function applyGuards(router){
  const { applyLogin } = useUserStore();
 router.beforeEach((to) => {
  if(to.meta.requiresAuth){
    console.log('test');
  }
 })
}
