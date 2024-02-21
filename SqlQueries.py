def drop_temp_tables():
    return "drop table if exists cobolcrossext_pgmcalled, cobolcrossext_datacalled, cobolcrossext_linkagedata, cobolcrossext_crosslinks"

def populate_cobolcrossext_pgmcalled():
    return """
    select distinct 
        split_part(clr.object_fullname,'.',2) as clrpgmname, 
        cle.object_name as clepgmname, 
        cle.object_fullname as clepgmfname
    into cobolcrossext_pgmcalled
    from 
        cdt_objects clr,
        ctv_links lnk,
        cdt_objects cle
    where 
        clr.object_type_str in ('Cobol Paragraph','Cobol Section')
    and cle.object_type_str='Cobol Program' 
    and lnk.caller_id=clr.object_id
    and lnk.called_id=cle.object_id
    and lnk.link_type_lo=2048 and lnk.link_type_hi=65536
    """

def idx_cobolcrossext_pgmcalled_clepgmname():    
    return "create index cobolcrossext_pgmcalled_clepgmname on cobolcrossext_pgmcalled(clepgmname)"

def populate_cobolcrossext_linkagedata():    
    return """
    select object_id, object_name, split_part(object_fullname,'.',2) as pgmname 
    into cobolcrossext_linkagedata 
    from cdt_objects 
    where object_type_str in ('Cobol Data') and object_fullname like '%.LINKAGE.%' escape ''
    """

def idx_cobolcrossext_linkagedata_pgmname(): 
    return "create index cobolcrossext_linkagedata_pgmname on cobolcrossext_linkagedata(pgmname)"
        
def populate_cobolcrossext_datacalled():
    return """
    select distinct clrpgmname, cledat.object_id as cledatid, cledat.object_name as cledatname
    into cobolcrossext_datacalled
    from 
    cobolcrossext_pgmcalled pgmcalled,    
    cobolcrossext_linkagedata cledat
    where
    pgmcalled.clepgmname = cledat.pgmname
    and exists (select 1 from acc where idcle=cledat.object_id and acctyplo & 16777216=16777216) -- Cobol Data is Accessed 
    """
    
def idx_cobolcrossext_datacalled_3col():    
    return "create index cobolcrossext_datacalled_3col on cobolcrossext_datacalled(clrpgmname,cledatname,cledatid)"
    
def populate_cobolcrossext_crosslinks():
    return """
    select distinct dat1.cledatid as idclr, dat2.cledatid as idcle
    into cobolcrossext_crosslinks
    from 
    cobolcrossext_datacalled dat1,
    cobolcrossext_datacalled dat2
    where
        dat1.clrpgmname=dat2.clrpgmname
    and dat1.cledatname=dat2.cledatname
    and dat1.cledatid !=dat2.cledatid
    """

def get_sql_nblinks_created():    
    return "select count(distinct (idclr, idcle)) from cobolcrossext_crosslinks"
