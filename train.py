import torch
import numpy as np
import copy
from tqdm import trange
from evaluate import evaluate
from torch_geometric.data import DataLoader
from torch_geometric.utils import negative_sampling

def train(model,link_predictor,emb,edge_index,split_edge,batch_size,optimizer,device):
    '''
    Train the model
    '''

    model.train()
    link_predictor.train()

    pos_train_edge = split_edge['train']['edge'].to(device)

    train_losses = []
    val_accs = []
    best_acc = 0
    best_model = None
    scheduler = None      

    for edge_id in DataLoader(trange(pos_train_edge.shape[0]), batch_size, shuffle=True):
		optimizer.zero_grad()

		node_emb = model(emb,edge_index)
		pos_edge = pos_train_edge[edge_id].T

		pos_pred = link_predictor(node_emb[pos_edge[0]], node_emb[pos_edge[1]])
		neg_edge = negative_sampling(edge_index, num_nodes=emb.shape[0],
									num_neg_samples=edge_id.shape[0], method='dense')

		neg_pred = link_predictor(node_emb[neg_edge[0]], node_emb[neg_edge[1]])

		loss =  -torch.log(pos_pred + 1e-15).mean() -torch.log(1 - neg_pred + 1e-15).mean()
		loss.backward()
		optimizer.step()

		train_losses.append(loss.item())

	return sum(train_losses)/len(train_losses)

    # if epoch % 10 == 0:
    #   val_acc = evaluate(val_loader, model)
    #   val_accs.append(val_acc)
    #   if val_acc > best_acc:
    #     best_acc = val_acc
    #     best_model = copy.deepcopy(model)
    # else:
    #   val_accs.append(val_accs[-1])
    
    # return val_accs, losses, best_model, best_acc