App.module('Page', function (Page) {
    // Module Must be Manually Started
    Page.startWithParent = false;
    // Router needs to be created immediately, regardless of
    // whether or not the module is started
    Page.controller = new Page.Controller();
    Page.router = new Page.Router({controller: Page.controller});
    Page.addFinalizer(function () {
        Page.controller.hide();
        Page.stopListening();
    });
});