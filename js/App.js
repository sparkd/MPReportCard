var App = (function () {
    var Application = Marionette.Application.extend({});
    var application = new Application();

    application.addRegions({
        search: '[data-region=search]',
        body: '[data-region=body]'
    });

    application.on('start', function () {
        Backbone.history.start();
    });

    return application;
})();