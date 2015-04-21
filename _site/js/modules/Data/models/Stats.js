App.module('Data', function (Data) {
    Data.Stats = Backbone.Model.extend({
        _cache: {},
        get_averages: function (type) {

            var govtPosts = this.get('govt_posts')

            // If we don't have the averages built, create and cache them
            if (_.isUndefined(this._cache[type])) {

                var _cache = this._cache[type] = {}
                var _data = this.get(type)

                // Loop through each of the party members, dividing the data
                // By the number of members
                _.each(this.get('party_members'), function (num_members, party) {
                    // If this is an EDMS or Answer, we want to remove
                    // Government posts
                    if (_.contains(['edms', 'answers'], type)){
                        if (!(_.isUndefined(govtPosts[party]))) {
                            num_members -= govtPosts[party]
                        }
                    }
                    _cache[party] = _data[party] / num_members
                });

                return this._cache[type]

            } else {
                return this._cache[type]
            }

        }

    });
});