DROP TABLE _rebel_votes;

CREATE TABLE _rebel_votes AS SELECT
                              m.id AS         member_id,
                              sum(CASE WHEN (mv.role = 'rebel' OR mv.role = 'rebel teller') AND result != 'both' THEN 1
                                  ELSE 0 END) rebel_votes
                            FROM members m LEFT JOIN members_votes mv ON mv.member_id = m.id
                            GROUP BY m.id;