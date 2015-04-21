App.module('MP', function (MP) {
    MP.Router = Marionette.AppRouter.extend({
        appRoutes: {
            "mp/:id": "showMP"
        }
    });
});