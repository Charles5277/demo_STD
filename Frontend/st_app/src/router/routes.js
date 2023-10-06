const routes = [
  {
    path: '/',
    component: () => import('layouts/layout_frame.vue'),
    children: [
      {
        path: '/',
        name: 'init',
        component: () => import('src/pages/init_page.vue'),
      },
      {
        path: '/test',
        name: 'test',
        component: () => import('src/pages/test_page.vue'),
      },
      {
        path: '/login',
        name: 'login',
        component: () => import('src/pages/login_page.vue'),
      },
      {
        path: '/lobby',
        name: 'lobby',
        component: () => import('src/pages/lobby_page.vue'),
      },
      {
        path: '/chatroom',
        name: 'room',
        component: () => import('src/pages/chat_room.vue'),
      },
    ],
  },
];

export default routes;
