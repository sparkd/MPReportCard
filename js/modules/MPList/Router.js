App.module('MPList', function (MPList) {
    MPList.Router = Marionette.AppRouter.extend({
        appRoutes: {
            "mp": "showMPs"
        }
    });
});