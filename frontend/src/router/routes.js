const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'upload-certificate', component: () => import('pages/UploadCertificate.vue') },
    ],
  },
]

export default routes
