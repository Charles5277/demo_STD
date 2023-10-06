import { boot } from 'quasar/wrappers'
import { VueFire, VueFireAuth } from 'vuefire'
import firebaseApp from '../firebase.js'

export default boot(({ app }) => {
  app.config.globalProperties.$firebase = firebaseApp;
  app.use(VueFire, {
    firebaseApp,
    modules: [
      VueFireAuth(),
    ],
  });
});
