App.Helpers = App.Helpers || {};
App.Helpers.SubAppManager = (function() {

    var SubAppManager = Marionette.Controller.extend({
        startSubApp: function(name, args) {
            var newApp = App.module(name);

            if (this.currentApp === newApp) {
                return;
            }

            if (this.currentApp) {
                this.currentApp.stop();
                // Nothing Responds to it, but can be an extension point
                App.vent.trigger('subapp:stopped', this.currentAppName);
            }

            this.currentApp = newApp;
            this.currentAppName = name;

            newApp.start(args);
            // Nothing Responds to it, but can be an extension point
            App.vent.trigger('subapp:started', name);
        }
    });

    var manager = new SubAppManager();
    App.commands.setHandler('subapp:start', manager.startSubApp, manager);

    return manager;

})();