from django.contrib.admin import AdminSite


class CustomAdmin(AdminSite):
    def get_app_list(self, request, **kwargs):
        app_list = super().get_app_list(request, kwargs)
        app_list += [
            {
                "name": "Analytics",
                "app_label": "other_actions_app",
                "models": [
                    {
                        "name": "Network traffic",
                        "object_name": "network statistics view",
                        "admin_url": 'traffic',
                    },
                    {
                        "name": "Top Movies/TV Shows",
                        "object_name": "top_media_view",
                        "admin_url": 'top-media',
                    }
                ],
            }
        ]
        return app_list


custom_admin = CustomAdmin()
