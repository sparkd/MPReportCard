App.module('MP', function (MP) {
    // Module Must be Manually Started
    MP.startWithParent = false;
    MP.controller = new MP.Controller();
    MP.router = new MP.Router({controller: MP.controller});
    MP.addFinalizer(function () {
        MP.controller.hide();
        MP.stopListening();
    });
});