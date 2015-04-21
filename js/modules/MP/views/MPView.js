App.module('MP', function (MP) {
    MP.MPView = Marionette.ItemView.extend({
        className: 'mp',
        template: '#mp',
        emptyTemplate: '#mp-404',

        initialize: function () {

            var _this = this
            var status = {}

            _.each(App.module('Data').averages, function( average, key ) {

                var value = _this.model.get(key)
                var tolerance_value = average * 0.05

                if (value >= (average - tolerance_value) && value <= (average + tolerance_value)) {
                    status[key] = 'average'
                } else if (value >= (average)) {
                    status[key] = 'Above average'
                } else {
                    status[key] = 'Below average'
                }

            });

            this.model.set('status', status)

        },

        templateHelpers: function () {
            return {
                getStatus: function (key) {


                    if (((key == 'answers' || key == 'edms') && this.govt) || (key == 'replies_percentage' && !this.data_quality_indicator)){
                        return '<div class="traffic-light na"></div>'
                    }

                    var status = this.status[key]
                    return '<div class="traffic-light ' + status.toLowerCase().replace(' ', '-') + '"><span>' + status + '</span></div>'

                },
                debates_description: function () {
                    return 'Has spoken ' + this.speeches + ' times in ' + this.debates + ' debates. On average, an MP spoke in ' + App.module('Data').averages['debates'] + ' debates.'
                },
                interests_description: function () {
                    var desc = 'Financial interests declared by ' + this.name + '. The MP average was &pound' + App.module('Data').averages['interests'].toLocaleString() + '.'
                    // Create link to google doc to view the interests
                    if (this.interests > 0){
                       desc += ' <a class="external" target="_blank" href="https://spreadsheets.google.com/tq?tqx=out:html&tq=SELECT+A,+B,+C,+D,+F,+G,+H,+I,+J,+K+WHERE+A=' + this.id + '+AND+I=FALSE&key=1j3IX-yGOZj1SUNMEs817v9egBPu5YJyVek26t3mGJqQ">View interests.</a>'
                    }
                    return desc

                },
                expenses_description: function () {
                    var mp_name = this.list_name.replace(/ /g,"_").replace(',', '').toLowerCase()
                    var desc = this.name + ' declared expenses totalling &pound' + this.expenses.toLocaleString() + ' in this parliament. The MP average was &pound' + App.module('Data').averages['expenses'].toLocaleString() + '.'
                    if (this.expenses > 0){
                        desc += ' <a class="external" target="_blank" href="http://datapipes.okfnlabs.org/csv/html/?url=https://raw.githubusercontent.com/sparkd/mp-expenses/master/data/' + mp_name +'.csv">View expenses.</a>'
                    }
                    return desc
                 },
                answers_description: function () {
                    if (this.govt){
                        return 'Government ministers do not submit written questions.'
                    }else{
                        return 'Received answers to ' +  this.answers + ' written questions. The MP average was ' + App.module('Data').averages['answers'] + '.'
                    }
                },
                votes_description: function () {
                    var desc = 'Attended ' + this.votes_attended + ' out of '  + this.votes_possible + ' votes.  The average attendance was ' + App.module('Data').averages['votes_percentage'] + '&#37;.'
                    desc += ' <a class="external" target="_blank" href="http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/' + this.pw_id + '&showall=yes">View votes.</a>'
                    return desc

                },
                replies_description: function () {

                    if(!this.data_quality_indicator){
                        return  'WriteToThem had no information on this MP.'
                    }else{
                        return  'Replied to ' + this.replies + ' out of '  + this.surveys + ' letters sent via WriteToThem in 2013. The average reply rate was ' + App.module('Data').averages['replies_percentage'] + '&#37;.'
                    }
                },
                rebel_votes_description: function () {
                    var desc = 'Voted against their party in ' + this.rebel_votes + ' votes. The MP average was ' + App.module('Data').averages['rebel_votes'] + '.'
                    if(this.rebel_votes){
                        desc += '<br /><a class="external" target="_blank" href="http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/' + this.pw_id + '&role=rebel">View rebellions.</a>'
                    }
                    return desc
                },
                edms_description: function () {
                    var desc
                    if (this.govt) {
                       desc = 'Government ministers do not submit Early Day Motions.'
                    }else{
                       desc = 'Signed ' + this.edms + ' Early Day Motions. The MP average was ' + App.module('Data').averages['edms'] + '.'

                       if(this.edms && this.edms_id){
                        desc += '<br /><a class="external" target="_blank" href="http://www.edms.org.uk/mps/' + this.edms_id + '">View EDMS.</a>'
                       }

                    }
                    return desc;
                }
            };
        },
        getTemplate: function () {
            if (this.model) {
                return this.template;
            }
            else {
                return this.emptyTemplate;
            }
        },
        onRender: function () {
            // Make mp page item active
            $('#navbar-collapse li').removeClass('active');
            $('#navbar-collapse li a[href="#mp"]').parent().addClass('active');
            window.scrollTo(0,0);
        }
    });
});