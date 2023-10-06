// > 由於重整頁面後資料會被清空，暫時不使用此檔案
import { defineStore } from 'pinia';

export const useUserStore = defineStore({
  id: 'user',
  state: () => ({
    uid: '',
    username: '',
    email: '',
    language: '',
  }),
  actions: {
    storeUserData(user) {
      this.uid = user.uid
      this.username = user.username
      this.email = user.email
      this.language = user.language
    },
  },
});
