App.module('MPList', function (MPList) {
    MPList.EmptyView = Marionette.ItemView.extend({
        tagName: 'tr',
        template: '#mplist-empty'
    });
});