App.module('Data', function(Data) {
    Data.MP = Backbone.Model.extend({
        initialize: function() {
            // Set the class name to for coloring the MP header etc.,
            this.set({ clsName: this.get("party_short").toLowerCase().replace(/ /g, '-') });
        }
    });
});