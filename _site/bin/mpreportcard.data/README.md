SETUP
-----

  sudo -u postgres createuser -S -D -R mp
  sudo -u postgres psql -c "ALTER USER mp with password 'asdf'"
  sudo -u postgres createdb -O mp mpreportcard -E UTF8
  
  Debates and questions come from: http://parser.theyworkforyou.com/hansard.html
  
  http://lda.data.parliament.uk/ Only goes back a year or so
  
  rsync -az --progress --exclude '.svn' --exclude 'tmp/' --relative data.theyworkforyou.com::parldata/scrapedxml/debates/debates201* .

  rsync -az --progress --exclude '.svn' --exclude 'tmp/' --relative data.theyworkforyou.com::parldata/scrapedxml/wrans/answers201* .
      
  
TODO
----

2. Join everything Up. 



  Start date is wrong - members
  
  



3. Evaluate what we've got.


Go through each one and make sure we get correct errors for missing MPs. EDMS is not working.


Need to be careful with EDMS: Need to put N/A.



Choropleth
http://bl.ocks.org/mbostock/4060606


https://github.com/dkastner/docker-solr-sunspot

http://solr.pl/en/2010/10/11/data-import-handler-%E2%80%93-how-to-import-data-from-sql-databases-part-1/



FRONT END
---------

Have grid and table view.
At the bottom, have a fixed summary?



FIXME:

We have a lot of missing financial interests!!!!!

Spoken in debates etc., is wrong according to they work for you. 
Because they go back to 2005!!! But still not write. What are the answers?




Tasks Workflow
--------------

They Work For You import into Mongo DB - and is just used to get data for image task

1. create table expenses_sum as select member_id, sum(value) from expenses e inner join members m on e.member_id = m.id group by member_id;


select m.id, sum(case when cq.type = 'oral_question' and cq.registered_interest = false then 1 else 0 end) oral, sum(case when cq.type = 'oral_question' and cq.registered_interest = true then 1 else 0 end) oral_reg_int,  sum(case when cq.type = 'written_question' and cq.registered_interest = false then 1 else 0 end) written, sum(case when cq.type = 'written_question' and cq.registered_interest = true then 1 else 0 end) written_reg_int from members m inner join commons_question cq on cq.tabling_member = m.id group by m.id;


The Sonics - Bad betty



Elastic search
--------------

http://docker:9200/_stats


Hinterland
by
LoneLady



  