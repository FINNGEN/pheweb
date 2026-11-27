import { TableColumnConfiguration } from "../../common/commonTableColumn";
import { SortingRule } from "react-table-v6";
import { Phenotype } from '../../common/commonModel';

export interface IndexConfiguration {
  banner?: string;
  table : { columns: TableColumnConfiguration<Phenotype> ,
            defaultSorted : SortingRule<Phenotype>[] }
  tableColumns: TableColumnConfiguration<Phenotype>;
}