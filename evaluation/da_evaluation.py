__author__ = 'snownettle'
from postgres import postgres_queries
from da_recognition import dialogue_acts_taxonomy
from tabulate import tabulate
from operator import itemgetter


def evaluation_taxonomy_da(taxonomy_name, cursor):
    da_names = postgres_queries.find_states(taxonomy_name, cursor)
    evaluation_data = list()
    for da_name in da_names:
        # da_name = da.tag
        relevant_docs = len(postgres_queries.find_all_da_occurances_taxonomy('segmentation',
                                                                                     da_name, taxonomy_name, cursor))
        tp, fp = find_tp_fp(taxonomy_name, da_name, cursor)
        # print da_name + '\t' + str(tp + fp) + '\t' + str(tp)
        precision = calculate_precision(tp, fp)
        recall = calculate_recall(tp, relevant_docs)
        f_measure = calculate_f_measure(precision, recall)
        da_evaluation = [da_name, precision, recall, f_measure, tp, fp, relevant_docs]
        evaluation_data.append(da_evaluation)
    # header_data = ['dialogue act name', 'precision', 'recall', 'F-measure']
    evaluation_data = sorted(evaluation_data, key=itemgetter(0))
    evaluation_dict = put_in_dict(evaluation_data)
    print_evaluation(taxonomy_name, evaluation_data, evaluation_dict)


def put_in_dict(evaluation_data):
    evaluation_dict = dict()
    for row in evaluation_data:
        evaluation_dict[row[0]] = {'precision': row[1], 'recall': row[2], 'f1': row[3], 'tp': row[4], 'fp': row[5],
                                   'relevant_doc': row[6]}
    return evaluation_dict


def find_tp_fp(taxonomy, da_name, cursor):
    tp = 0
    fp = 0
    records = postgres_queries.find_all_da_occurances_taxonomy('Segmentation_Prediction', da_name, taxonomy, cursor)
    for record in records:
        tweet_id = record[0]
        start_offset = record[1]
        end_offset = record[2]
        da = record[3]
        da_gs = postgres_queries.find_da_for_segment(tweet_id, start_offset, end_offset, taxonomy, cursor)
        if da == da_gs:
            tp += 1
        else:
            fp += 1
    return tp, fp


def calculate_precision(tp, fp):
    if (tp+fp) == 0:
        return 0
    else:
        precision_value = tp/float(tp+fp)
        return precision_value

def calculate_recall(tp, relevant_documents):
    if (tp+relevant_documents) == 0:
        return 0
    else:
        recall_value = tp/float(relevant_documents)
        return recall_value

def calculate_f_measure(precision, recall):
    if (recall + precision) ==0:
        return 0
    else:
        f_measure_value = 2*recall*precision/float(recall + precision)
        return f_measure_value


def print_evaluation(taxonomy, evaluation_data, evaluation_dict):
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Evaluation for ' + taxonomy + ' taxonomy'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print tabulate(evaluation_data, headers=['dialogue act name', 'precision', 'recall', 'F-measure',
                                             'True Positive', 'False Positive', 'Relevant Documents'])
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Overall evaluation for ' + taxonomy + ' taxonomy'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    evaluation_data_micro_macro = overall_evaluation(evaluation_dict)
    print tabulate(evaluation_data_micro_macro, headers=[' ', 'precision', 'recall', 'F-measure',
                                             'True Positive', 'False Positive', 'Relevant Documents'])


def overall_evaluation(evaluation_dict):
    evaluation_data = list()
    recall = 0
    precision = 0
    tp = 0
    fp = 0
    rd = 0
    for da, values in evaluation_dict.iteritems():
        recall += values['recall']
        precision += values['precision']
        tp += values['tp']
        fp += values['fp']
        rd += values['relevant_doc']
    classification_numbers = len(evaluation_dict.values())
    average_pr = precision/float(classification_numbers)
    average_re = recall/float(classification_numbers)
    average_f1 = 2*average_pr*average_re/float(average_pr+average_re)
    da_evaluation = ['Macro-average Method', average_pr, average_re, average_f1]
    evaluation_data.append(da_evaluation)
    micro_pr = tp/float(tp+fp)
    micro_re = tp/float(rd)
    micro_f1 = 2*micro_pr*micro_re/float(micro_pr+micro_re)
    da_evaluation = ['Micro-average Method', micro_pr, micro_re, micro_f1]
    evaluation_data.append(da_evaluation)
    return evaluation_data
