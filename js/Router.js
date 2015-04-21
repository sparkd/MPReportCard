App.Router = Marionette.AppRouter.extend({
    routes: {
        "notFound": "redirectNotFound"
    },
    redirectNotFound: function () {
        Backbone.history.navigate('', { trigger: true, replace: true});
    }
});

App.addInitializer(function () {
    App.router = new App.Router();
});