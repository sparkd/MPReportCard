App.module('MPList', function (MPList) {
    MPList.RowView = Marionette.ItemView.extend({
        tagName: 'tr',
        template: '#mplist-row'
    });
});