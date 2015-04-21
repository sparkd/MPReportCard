App.module('Data', function (Data) {
    Data.addInitializer(function (options) {
        // Data is passed in from the initialisation function
        Data.mps = new Data.MPs((options && options.data && options.data.mps) || []);
        Data.stats = new Data.Stats((options && options.data && options.data.stats) || []);
        // We don't need a model for the totals
        Data.averages = (options && options.data && options.data.averages) || [];
    });
    Data.addFinalizer(function () {
        // Delete the data
        delete Data.mps;
        delete Data.averages;
        delete Data.stats;
    });
});