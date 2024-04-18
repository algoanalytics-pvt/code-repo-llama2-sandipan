import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

llama2_data = pd.read_csv("ragas_evaluation_llama2_instructor.csv",index_col=0)
codellama_data = pd.read_csv("ragas_evauation_codellama_instructor.csv", index_col=0)


llama2_cont_util = np.array(llama2_data['context_utilization'])
llama2_faith = np.array(llama2_data['faithfulness'])
llama2_ans_rel = np.array(llama2_data['answer_relevancy'])
llama2_cont_prec = np.array(llama2_data['context_precision'])
llama2_cont_recall = np.array(llama2_data['context_recall'])
llama2_ans_corrt = np.array(llama2_data['answer_correctness'])

codellama_cont_util = np.array(codellama_data['context_utilization'])
codellama_faith = np.array(codellama_data['faithfulness'])
codellama_ans_rel = np.array(codellama_data['answer_relevancy'])
codellama_cont_prec = np.array(codellama_data['context_precision'])
codellama_cont_recall = np.array(codellama_data['context_recall'])
codellama_ans_corrt = np.array(codellama_data['answer_correctness'])

def plot_llama2_3d():
    x_ticks_labels = [f'Q{i}' for i in range(1,11)]
    y_ticks_labels = ['context_utilization','context_precision','context_recall','faithfulness','answer_relevancy', 'answer_correctness']

    z_values_llama = np.concatenate((llama2_cont_util,llama2_cont_prec,llama2_cont_recall,llama2_faith,llama2_ans_rel,llama2_ans_corrt))
    z_values_llama = np.reshape(z_values_llama,(10,6))

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    x_values = [i for i in range(1,11)]
    y_values = [i for i in range(1,7)]

    X,Y = np.meshgrid(x_values,y_values)
    print(llama2_ans_corrt)
    ax.set_xticks(x_values)
    ax.set_xticklabels(x_ticks_labels)
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_ticks_labels)

    ax.scatter(X,Y,z_values_llama,color='r')
    # ax.scatter(X,Y,z_values_codellama, color = 'g')
    plt.show()

def plot_codellama_3d():
    x_ticks_labels = [f'Q{i}' for i in range(1,11)]
    y_ticks_labels = ['context_utilization','context_precision','context_recall','faithfulness','answer_relevancy', 'answer_correctness']
    
    z_values_codellama = np.concatenate((codellama_cont_util,codellama_cont_prec,codellama_cont_recall,codellama_faith,codellama_ans_rel,codellama_ans_corrt))
    z_values_codellama = np.reshape(z_values_codellama,(10,6))
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    x_values = [i for i in range(1,11)]
    y_values = [i for i in range(1,7)]

    X,Y = np.meshgrid(x_values,y_values)
    print(llama2_ans_corrt)
    ax.set_xticks(x_values)
    ax.set_xticklabels(x_ticks_labels)
    ax.set_yticks(y_values)
    ax.set_yticklabels(y_ticks_labels)

    ax.scatter(X,Y,z_values_codellama,color='r')
    plt.show()
    
