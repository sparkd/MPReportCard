App.module('MPList', function (MPList) {
    // Module Must be Manually Started
    MPList.startWithParent = false;
    // Router needs to be created immediately, regardless of
    // whether or not the module is started
    MPList.controller = new MPList.Controller();
    MPList.router = new MPList.Router({controller: MPList.controller});

    MPList.addInitializer(function () {
        MPList.controller.show();
    });

    MPList.addFinalizer(function () {
        MPList.controller.hide();
        MPList.stopListening();
    });
});