def drop_temp_tables():
    return "drop table if exists crossext_pgmcalled, crossext_datcalled, crossext_crosslinks"

def populate_crossext_pgmcalled():
    return """
    select distinct split_part(clr.object_fullname,'.',2) as clrpgmname, cle.keynam as clepgmname
    into crossext_pgmcalled
    from 
    cdt_objects clr,
    ctv_links lnk,
    keys cle
    where 
        clr.object_type_str in ('Cobol Paragraph','Cobol Section')
    and cle.objtyp=545 --'Cobol Program' 
    and lnk.caller_id=clr.object_id
    and lnk.called_id=cle.idkey
    and lnk.link_type_lo=2048 and lnk.link_type_hi=65536 -- Cp links
    """

def idx_crossext_pgmcalled_clepgmname():    
    return "create index crossext_pgmcalled_clepgmname on crossext_pgmcalled(clepgmname)"
    
def populate_crossext_datcalled():
    return """
    select pgmcalled.clrpgmname, cledat.object_id as cledatid, cledat.object_name as cledatname
    into crossext_datcalled
    from 
    crossext_pgmcalled pgmcalled,    
    cdt_objects clrart,
    acc,
    cdt_objects cledat
    where
        clrart.object_type_str in ('Cobol Paragraph','Cobol Section')
    and split_part(clrart.object_fullname,'.',2)=pgmcalled.clepgmname
    and cledat.object_fullname like '%.LINKAGE.%'
    and cledat.object_type_str='Cobol Data'
    and acc.idclr=clrart.object_id
    and acc.idcle=cledat.object_id
    and acc.acctyplo & 16777216=16777216 -- Access
    """
    
def idx_crossext_datcalled_3col():    
    return "create index crossext_datcalled_3col on crossext_datcalled(clrpgmname,cledatname,cledatid)"
    
def populate_crossext_crosslinks():
    return """
    select distinct dat1.cledatid as idclr, dat2.cledatid as idcle
    into crossext_crosslinks
    from 
    crossext_datcalled dat1,
    crossext_datcalled dat2
    where
        dat1.clrpgmname=dat2.clrpgmname
    and dat1.cledatname=dat2.cledatname
    and dat1.cledatid !=dat2.cledatid
    """

def get_sql_nblinks_created():    
    return "select count(distinct (idclr, idcle)) from crossext_crosslinks"

