App.module('Page', function (Page) {
    Page.Router = Marionette.AppRouter.extend({
        appRoutes: {
            "": "showIndex",
            "about": "showAbout"
        }
    });
});