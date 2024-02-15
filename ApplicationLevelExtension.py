import cast_upgrade_1_6_13 # @UnusedImport
import logging
import SqlQueries as sqlq
from cast.application import ApplicationLevelExtension

class ApplicationLevelExtension(ApplicationLevelExtension):
    '''
    classdocs
    '''

    def end_application(self, application):
        logging.info('##################################################################')
        kb=application.get_knowledge_base()
        logging.info('Populating work tables...')
        kb.execute_query(sqlq.drop_temp_tables())        
        logging.info('(1/5)')
        kb.execute_query(sqlq.populate_crossext_pgmcalled())
        logging.info('(2/5)')
        kb.execute_query(sqlq.idx_crossext_pgmcalled_clepgmname())
        logging.info('(3/5)')
        kb.execute_query(sqlq.populate_crossext_datcalled())
        logging.info('(4/5)')
        kb.execute_query(sqlq.idx_crossext_datcalled_3col())
        logging.info('(5/5)')
        kb.execute_query(sqlq.populate_crossext_crosslinks())                
        nblinks_rs=kb.execute_query(sqlq.get_sql_nblinks_created())
        for row in nblinks_rs:
            nblinks=row[0]
        logging.info('***********************************')
        logging.info('Links about to be created: '+str(nblinks))
        logging.info('***********************************')        
        logging.info('Creating links...')
        application.update_cast_knowledge_base("Create links between Cobol Data items", """        
        insert into CI_LINKS (CALLER_ID, CALLED_ID, LINK_TYPE, ERROR_ID)        
        select distinct idclr, idcle, 'referLink', 0
        from crossext_crosslinks
        """)
        logging.info('Done.')
        logging.info('##################################################################')
