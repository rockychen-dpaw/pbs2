#!/bin/bash
function execute_sql(){
    if [[ "$targetuser" == "" ]]; then
        echo $(psql -h $targethost -p $targetport -d $targetdatabase -c "$1")
    else
        echo $(PGPASSWORD=$targetpassword psql -h $targethost -p $targetport -d $targetdatabase -c "$1")
    fi
}

function query() {
    local sql=$1
    local database=$2
    if [[ "${database}" == "" ]]; then
        database="target"
    fi
    if [[ "${database}" == "target" ]]; then
        if [[ "$targetuser" == "" ]]; then
            results=$(psql -h $targethost -p $targetport -d $targetdatabase -c "${sql}")
        else
            results=$(PGPASSWORD=$targetpassword psql -h $targethost -p $targatport -d $targetdatabase -U $targetuser -c "${sql}")
        fi
    else
        if [[ "$sourceuser" == "" ]]; then
            results=$(psql -h $sourcehost -p $sourceport -d $sourcedatabase -c "${sql}")
        else
            results=$(PGPASSWORD=$sourcepassword psql -h $sourcehost -p $sourceport -d $sourcedatabase -U $sourceuser -c "${sql}")
        fi
    fi
    IFS=$'\n'
    row_index=0
    for row in ${results}; do
        if [[ $row_index -lt 2 ]]; then
            row_index=$(($row_index + 1))
            continue
        elif [[ "$row" == \(* ]]; then
            break
        else
            echo $(echo -e "${row}" | sed -e 's/^\s\{1,\}//' -e 's/\s\{1,\}$//')
        fi
        row_index=$(($row_index + 1))
    done
}

function execute_file(){
    if [[ "$targetuser" == "" ]]; then
        echo $(psql -h $targethost -p $targetport -d $targetdatabase -f "$1")
    else
        echo $(PGPASSWORD=$targetpassword psql -h $targethost -p $targetport -d $targetdatabase -f "$1")
    fi
}

function contains() { 
    local in=0
    local -n array=$1
    for t in "${array[@]}"; do
        if [[ $2 == $t* ]] ; then
            in=1
            break
        fi
    done
    echo $in
}

function remove_element(){
    local -n array=$1
    for i in "${!array[@]}"; do
        if [[ "${array[i]}" == "$2" ]]; then
            unset 'array[i]'
            break
        fi
    done
}

function to_tablestring(){
    local -n array=$1
    local table_string=""
    for t in "${array[@]}"; do
        if [[ "${table_string}" == "" ]]; then
            table_string="'${t}'"
        else
            table_string="${table_string},'${t}'"
        fi

    done

    echo ${table_string}
}

currentdir=$(pwd)
scriptpath=$(dirname "$0")
cd $scriptpath
scriptpath=$(pwd)
cd $currentdir
migrationroot="/tmp/pbsmigration"

source $scriptpath/.setenv.sh

dump_data=0
clear_data=0
import_data=0
continue_import=0
sync_media=0
if [[ "$1" == "data" ]] && [[ "$2" == "dump" ]]; then
    dump_data=1
elif [[ "$1" == "data" ]] && [[ "$2" == "import" ]]; then
    import_data=1
    if [[ "$3" == "continue" ]] ; then
        continue_import=1
    fi
elif [[ "$1" == "data" ]] && [[ "$2" == "" ]]; then
    dump_data=1
    import_data=1
elif [[ "$1" == "media" ]]; then
    sync_media=1
elif [[ "$1" == "clear" ]]; then
    clear_data=1
elif [[ "$1" == "" ]]; then
    dump_data=1
    import_data=1
    sync_media=1
fi

#create the migrationroot path if it does not exist
if [[ ! -d ${migrationroot} ]]; then
    mkdir ${migrationroot}
fi

#remove the data migration folder if dumping data is required
if [[ $dump_data -eq 1 ]]; then
    if [[ -d "${migrationroot}/database" ]]; then
        rm -rf "${migrationroot}/database"
    fi
fi

#create the data migration folder if it does not exist
if [[ $dump_data -eq 1 ]] || [[ $import_data -eq 1 ]]; then
    if [[ ! -d "${migrationroot}/database" ]]; then
        mkdir "${migrationroot}/database"
    fi
    if [[ ! -d "${migrationroot}/database/step1" ]]; then
        mkdir "${migrationroot}/database/step1"
    fi
    if [[ ! -d "${migrationroot}/database/step2" ]]; then
        mkdir "${migrationroot}/database/step2"
    fi
fi

if [[ $continue_import -eq 0 ]]; then
    rm -f "${migrationroot}/database/step1_importedtables.txt"
fi

if [[ "$pbshome" == "" ]]; then
    pbshome=$(dirname "$scriptpath")
fi

declare step1_tables=()
declare -A table_rowcount=()
declare imported_tables=()
if [[ $dump_data -eq 1 ]]; then
    sql="select a.relname from pg_class a join pg_namespace b on a.relnamespace=b.oid where b.nspname='${targetschema}' and a.relkind='r' order by a.relname"
    for table in $(query "${sql}"); do
        if [[ "${step1_included_tables}"  != "" ]] && [[ ${#step1_included_tables[@]} -gt 0  ]]; then
            if [[ $(contains step1_included_tables ${table}) -eq 1 ]]; then
                step1_tables+=($table)
            else
                continue;
            fi
        elif [[ "${step1_excluded_tables}"  != "" ]] && [[ ${#step1_excluded_tables[@]} -gt 0 ]] && [[ $(contains step1_excluded_tables ${table}) -eq 1 ]]; then
            continue;
        else
            step1_tables+=($table)
        fi
    done 

    #find each table's row count
    for table in "${step1_tables[@]}"; do
        echo "Retrive ${table}'s row count "
        row_count=$(query "select count(*) from ${sourceschema}.${table}" "source") 
        table_rowcount[${table}]=$row_count
        echo "${table} ${row_count}" >> ${migrationroot}/database/tables_rowcount.txt
    done

    #dump the data
    for table in "${step1_tables[@]}"; do
        if [[ $(contains step1_tables ${table}) -eq 0 ]]; then
            continue;
        fi
        echo "dump table '${table}'"
        if [[ "$sourceuser" == "" ]]; then
            if [[ "${step1_include_schema_tables}"  != "" ]] && [[ ${#step1_include_schema_tables[@]} -gt 0 ]] && [[ $(contains step1_include_schema_tables ${table}) -eq 1 ]]; then
                pg_dump --column-inserts -n $sourceschema -t $table -h $sourcehost -p $sourceport -d $sourcedatabase -f ${migrationroot}/database/step1/$table.sql
            else
                pg_dump -a --column-inserts -n $sourceschema -t $table -h $sourcehost -p $sourceport -d $sourcedatabase -f ${migrationroot}/database/step1/$table.sql
            fi
        else
            if [[ "${step1_include_schema_tables}"  != "" ]] && [[ ${#step1_include_schema_tables[@]} -gt 0 ]] && [[ $(contains step1_include_schema_tables ${table}) -eq 1 ]]; then
                PGPASSWORD=$sourcepassword pg_dump --column-inserts -n $sourceschema -t $table -h $sourcehost -p $sourceport -d $sourcedatabase -U $sourceuser -f ${migrationroot}/database/step1/$table.sql
            else
                PGPASSWORD=$sourcepassword pg_dump -a --column-inserts -n $sourceschema -t $table -h $sourcehost -p $sourceport -d $sourcedatabase -U $sourceuser -f ${migrationroot}/database/step1/$table.sql
            fi
        fi
    done
else
    #find each table's row count
    echo "Try to retrieve table's row count from file "
    while IFS=' ' read -r table row_count; do
        table_rowcount[${table}]=${row_count}
        echo "${table} ${table_rowcount[$table]}"
    done < "${migrationroot}/database/tables_rowcount.txt"
    #find the tables to import
    for table in  $(ls ${migrationroot}/database/step1); do
        table=${table%.sql}
        if [[ "${step1_included_tables}"  != "" ]] && [[ ${#step1_included_tables[@]} -gt 0  ]]; then
            if [[ $(contains step1_included_tables ${table}) -eq 1 ]]; then
                step1_tables+=($table)
                echo "Found table ${table} ${table_rowcount[$table]}"
            else
                continue;
            fi
        elif [[ "${step1_excluded_tables}"  != "" ]] && [[ ${#step1_excluded_tables[@]} -gt 0 ]] && [[ $(contains step1_excluded_tables ${table}) -eq 1 ]]; then
            continue;
        else
            step1_tables+=($table)
            echo "Found table ${table} ${table_rowcount[$table]}"
        fi
    done 
    #find imported tables
    if [[ ${continue_import} -eq 1 ]] && [[ -e "${migrationroot}/database/step1_importedtables.txt" ]]; then
        echo "Try to find already imported tables"
        while IFS='' read -r table; do
            imported_tables+=(${table})
            echo "${table} already imported"
        done < "${migrationroot}/database/step1_importedtables.txt"
    fi
fi

if [[ ${import_data} -eq 1 ]]; then
    #find the import order through schema
    all_tables=()
    ordered_tables=()
    sql="SELECT a.relname FROM pg_class a JOIN pg_namespace b ON a.relnamespace = b.oid WHERE b.nspname= '${targetschema}' and a.relkind='r'"
    for table in $(query "${sql}"); do
        all_tables+=("${table}")
    done
    #find the tables which have not any foreign keys
    while [[ ${#all_tables[@]} -gt 0  ]]; do
        if [[ ${#ordered_tables[@]} -eq 0 ]]; then
            sql="SELECT a.relname FROM pg_class a JOIN pg_namespace b ON a.relnamespace = b.oid WHERE b.nspname= '${targetschema}' and a.relkind='r' and not exists(select 1 from pg_constraint c where c.conrelid=a.oid and c.contype='f')"
        else
            sql="SELECT a.relname FROM pg_class a JOIN pg_namespace b ON a.relnamespace = b.oid WHERE b.nspname= '${targetschema}' and a.relkind='r' and a.relname not in ($(to_tablestring ordered_tables)) and not exists(select 1 from pg_constraint c join pg_class d on c.confrelid = d.oid where c.conrelid=a.oid and c.contype='f' and d.relnamespace = b.oid and d.relname not in ($(to_tablestring ordered_tables)) )"
        fi
        for table in $(query "${sql}"); do
            ordered_tables+=("${table}")
            remove_element all_tables "${table}"
        done
    done
    
    #add column 'name' to django_content_type for data migration

    #clear data first
    for (( idx=${#ordered_tables[@]}-1 ; idx>=0 ; idx-- )) ; do
        table="${ordered_tables[idx]}"
        if [[ $(contains step1_tables ${table}) -eq 1 ]] && [[ $(contains imported_tables ${table}) -eq 0 ]]; then
            if [[ "${step1_include_schema_tables}"  != "" ]] && [[ ${#step1_include_schema_tables[@]} -gt 0 ]] && [[ $(contains step1_include_schema_tables ${table}) -eq 1 ]]; then
                echo "Drop table '${table}'"
                execute_sql "drop table ${targetschema}.${table}"
            else
                echo "Clean table '${table}'"
                execute_sql "delete from ${targetschema}.${table}"
            fi
        fi
    done

    for table in "${ordered_tables[@]}"; do
        if [[ $(contains step1_tables ${table}) -eq 1 ]] && [[ $(contains imported_tables ${table}) -eq 0 ]]; then
            echo "Importing table '${table}', ${table_rowcount[$table]} rows"
            if [[ "${table}" == "django_content_type" ]]; then
                execute_sql "alter table ${targetschema}.${table} add column name varchar(100)"
            elif [[ "${table}" == "review_prescribedburn" ]]; then
                execute_sql "alter table ${targetschema}.${table} rename column region_id to region"
            fi
            execute_file "${migrationroot}/database/step1/${table}.sql" >/dev/null
            if [[ "${table}" == "django_content_type" ]]; then
                execute_sql "alter table ${targetschema}.${table} drop column name"
            elif [[ "${table}" == "review_prescribedburn" ]]; then
                execute_sql "alter table ${targetschema}.${table} rename column region to region_id"
            fi
            imported_row_count=$(query "select count(*) from ${targetschema}.${table}" "target")
            if [[ ${table_rowcount[$table]} -eq ${imported_row_count} ]]; then
                echo "${imported_row_count} rows were imported."
                echo ${table} >> "${migrationroot}/database/step1_importedtables.txt"
            else
                echo "Import failed, ${imported_row_count}/${table_rowcount[$table]} rows were imported"
                exit 1
            fi
        fi
    done
fi

#refresh record links
echo "Migration finished"
