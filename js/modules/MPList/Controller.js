App.module('MPList', function (MPList) {
    MPList.Controller = Marionette.Controller.extend({
        // When the module starts, we need to make sure we have
        // the correct view showing
        show: function () {
        // No Special Setup
        },
        // When the module stops, we need to clean up our views
        hide: function () {
            App.body.close();
            this.data = this.view = null;
        },
        // Show list of MPs
        showMPs: function () {
            this._ensureSubAppIsRunning();
            this.data = App.module('Data').mps;
            this.view = new MPList.TableView({collection: this.data});
            // Show in the body
            App.body.show(this.view);
        },
        // Makes sure that this subapp is running so that we can
        // perform everything we need to
        _ensureSubAppIsRunning: function () {
            App.execute('subapp:start', 'MPList');
        }
    });
});