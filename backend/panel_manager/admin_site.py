from django.contrib.admin import AdminSite
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst


class PanelAdminSite(AdminSite):
    site_header = "Панель менеджера Страна"
    site_title = "Панель менеджера Страна"
    index_title = "Панель менеджера Страна"

    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {m: m_a for m, m_a in self._registry.items() if m._meta.app_label == label}
        else:
            models = self._registry

        for model, model_admin in models.items():
            admin_label = getattr(model_admin, "admin_label", None)
            app_label = model._meta.app_label
            if not admin_label:
                admin_label = app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                "name": capfirst(model._meta.verbose_name_plural),
                "object_name": model._meta.object_name,
                "perms": perms,
                "admin_url": None,
                "add_url": None,
            }
            if perms.get("change") or perms.get("view"):
                model_dict["view_only"] = not perms.get("change")
                try:
                    model_dict["admin_url"] = reverse(
                        "admin:%s_%s_changelist" % info, current_app=self.name
                    )
                except NoReverseMatch:
                    pass
            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse("admin:%s_%s_add" % info, current_app=self.name)
                except NoReverseMatch:
                    pass

            if admin_label in app_dict:
                app_dict[admin_label]["models"].append(model_dict)
            else:
                app_dict[admin_label] = {
                    "name": admin_label,
                    "app_label": app_label,
                    "app_url": reverse(
                        "admin:app_list",
                        kwargs={"app_label": app_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        if label:
            return app_dict.get(label)
        return app_dict


panel_site = PanelAdminSite(name="panel_site")
