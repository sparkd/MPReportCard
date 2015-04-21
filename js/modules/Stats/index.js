App.module('Stats', function (Stats) {
    // Module Must be Manually Started
    Stats.startWithParent = false;
    Stats.controller = new Stats.Controller();
    Stats.router = new Stats.Router({controller: Stats.controller});
    Stats.addFinalizer(function () {
        Stats.controller.hide();
        Stats.stopListening();
    });
});