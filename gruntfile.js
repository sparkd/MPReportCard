module.exports = function (grunt) {
    grunt.initConfig({
        uglify: {
            js: {
                files: {
                    'dist/all.min.js': [
                        'vendor/bower/jquery/dist/jquery.min.js',
                        'vendor/bower/underscore/underscore.js',
                        'vendor/bower/backbone/backbone.js',
                        'vendor/bower/marionette/lib/backbone.marionette.min.js',
                        'vendor/bower/devbridge-autocomplete/dist/jquery.autocomplete.min.js',
                        'vendor/stupidtable.min.js',
                        'vendor/bower/bootstrap/dist/js/bootstrap.min.js',
                        'vendor/bower/d3/d3.min.js',
                        'vendor/bower/d3-tip/index.js',
                        'vendor/bower/approximate-number/lib/approximate-number.js',

                        <!-- App and Helpers -->
                        'js/App.js',
                        'js/helpers/SubAppManager.js',
                        'js/Router.js',

                        <!-- Data -->
                        'js/modules/Data/models/MP.js',
                        'js/modules/Data/models/MPs.js',
                        'js/modules/Data/models/Stats.js',
                        'js/modules/Data/index.js',

                        <!-- Modules -->
                        'js/modules/MPList/views/RowView.js',
                        'js/modules/MPList/views/EmptyView.js',
                        'js/modules/MPList/views/TableView.js',
                        'js/modules/MPList/Controller.js',
                        'js/modules/MPList/Router.js',
                        'js/modules/MPList/index.js',

                        'js/modules/Page/views/IndexView.js',
                        'js/modules/Page/views/AboutView.js',
                        'js/modules/Page/Controller.js',
                        'js/modules/Page/Router.js',
                        'js/modules/Page/index.js',

                        'js/modules/MP/views/MPView.js',
                        'js/modules/MP/Controller.js',
                        'js/modules/MP/Router.js',
                        'js/modules/MP/index.js',

                        'js/modules/Stats/views/StatsView.js',
                        'js/modules/Stats/Controller.js',
                        'js/modules/Stats/Router.js',
                        'js/modules/Stats/index.js',

                        'js/modules/Search/views/SearchView.js',

                        <!-- Source data -->
                        'js/data.js',

                        <!-- Init -->
                        'js/initialize.js'
                    ]

                }
            }
        },

        // define source files and their destinations
        options: {
            sourceMap: true
        }

    });

    // load plugins
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // register at least this one task
    grunt.registerTask('default', [ 'uglify']);

};