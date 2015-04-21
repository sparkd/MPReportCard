App.module('Data', function (Data) {
    Data.MPs = Backbone.Collection.extend({
        model: Data.MP,
        _cache: {},
        get_stats: function(attr) {
            // Return a sorted array of stats for a particular attribute

            // Try and retrieve from cache first
            if (_.isUndefined(this._cache[attr])) {

                var arr = []
                this.each( function(model) {
                    arr.push({
                        key: model.get('name'),
                        value: model.get(attr),
                        party: model.get('party')
                    });
                  }, this );

                arr.sort(function(a, b) { return a.value - b.value; });

                // Add to the cache
                this._cache[attr] = arr

            }
            return this._cache[attr]

        }

    });
});