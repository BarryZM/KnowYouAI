from torch import nn
from torch import optim
import torch
import math
import os
import json
from torch.nn import functional as F

def get_w2i4matchnet(path):
    return json.load(open(path, "r", encoding="utf-8"))


def cut_word4matchnet(string):
    return list(string)


class MatchNet(nn.Module):
    """
    孪生网络
    """

    def __init__(self, word_size, embedding_dim):
        super(MatchNet, self).__init__()
        self.embedding_size = embedding_dim
        self.embedding = nn.Embedding(word_size, embedding_dim=embedding_dim)
        self.act = nn.ReLU(True)
        self.linear = nn.Linear(128 * 3, 64)
        # 多尺度，表示2-gram和3-gram
        self.query_conv_2 = nn.Sequential(
            nn.Conv2d(in_channels=1,
                      out_channels=64,
                      kernel_size=(2, embedding_dim),
                      stride=1,
                      padding=0),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.query_conv_3 = nn.Sequential(
            nn.Conv2d(in_channels=1,
                      out_channels=64,
                      kernel_size=(3, embedding_dim),
                      stride=1,
                      padding=0),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )

        self.response_conv_2 = nn.Sequential(
            nn.Conv2d(in_channels=1,
                      out_channels=64,
                      kernel_size=(2, embedding_dim),
                      stride=1,
                      padding=0),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.response_conv_3 = nn.Sequential(
            nn.Conv2d(in_channels=1,
                      out_channels=64,
                      kernel_size=(3, embedding_dim),
                      stride=1,
                      padding=0),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )

        conv1_size = "5_5_64"
        pool1_size = "10_10"
        conv2_size = "3_3_64"
        pool2_size = "5_5"
        self.conv1_size = [int(_) for _ in conv1_size.split("_")]
        self.pool1_size = [int(_) for _ in pool1_size.split("_")]
        self.conv2_size = [int(_) for _ in conv2_size.split("_")]
        self.pool2_size = [int(_) for _ in pool2_size.split("_")]

        self.conv1 = torch.nn.Conv2d(in_channels=1,
                                     out_channels=self.conv1_size[-1],
                                     kernel_size=tuple(
                                         self.conv1_size[0:2]),
                                     padding=0,
                                     bias=True
                                     )
        # torch.nn.init.kaiming_normal_(self.conv1.weight)
        self.conv2 = torch.nn.Conv2d(in_channels=self.conv1_size[-1],
                                     out_channels=self.conv2_size[-1],
                                     kernel_size=tuple(
                                         self.conv2_size[0:2]),
                                     padding=0,
                                     bias=True
                                     )
        self.pool1 = torch.nn.AdaptiveMaxPool2d(tuple(self.pool1_size))
        self.pool2 = torch.nn.AdaptiveMaxPool2d(tuple(self.pool2_size))

        self.output = nn.Sequential(
            nn.Linear(64 * 4 + 1 + self.pool2_size[0] * self.pool2_size[1] * self.conv2_size[-1], 256),
            nn.ReLU(True),
            nn.Linear(256, 1),
            # nn.Sigmoid()
        )

        self.sim = nn.Bilinear(128, 128, 1)  # y = xTAx + b 特征组合

    def forward(self, query, response):
        batch = query.size(0)
        emb1 = self.embedding(query).unsqueeze(1)
        emb2 = self.embedding(response).unsqueeze(1)
        o1 = self.query_conv_2(emb1)
        o2 = self.query_conv_3(emb1)
        query_v = torch.cat((
            o1.view(batch, -1),
            o2.view(batch, -1)
        ), dim=1)
        o1 = self.response_conv_2(emb2)
        o2 = self.response_conv_3(emb2)
        response_v = torch.cat((
            o1.view(batch, -1),
            o2.view(batch, -1)
        ), dim=1)
        sim = self.sim.forward(query_v, response_v).view(batch, -1)

        emb1 = self.embedding(query)
        emb2 = self.embedding(response)
        img = torch.matmul(emb1, emb2.transpose(1, 2)) / math.sqrt(self.embedding_size)
        batch, h, w = img.size()
        #
        simi_img = img.view(batch, 1, h, w)
        simi_img = F.relu(self.conv1(simi_img))
        simi_img = self.pool1(simi_img)
        simi_img = F.relu(self.conv2(simi_img))
        simi_img = self.pool2(simi_img)
        simi_img = simi_img.squeeze(1).view(batch, -1)

        feautre = torch.cat((query_v, response_v, sim, simi_img), dim=1)
        out = self.output(feautre)
        return out


class Matcher:
    def __init__(self, word_size, embedding_dim):
        self.match_net = MatchNet(word_size, embedding_dim)
        self.opt = optim.Adam(self.match_net.parameters(), lr=1e-4)
        self.loss_calc = nn.BCEWithLogitsLoss()
        relu = nn.ReLU()
        self.hingle_loss = lambda x: relu(x).mean()
        self.acc = 0
        self.iter_number = 0

    def train_on_batch(self, query, response, label):
        query = torch.tensor(query).long()
        response = torch.tensor(response).long()
        label = torch.tensor(label).float()
        ################## train
        self.match_net.train()
        output = self.match_net.forward(query, response)
        loss = self.loss_calc(output, label)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()
        #################### test
        self.match_net.eval()
        with torch.no_grad():
            score = self.match_net.forward(query, response)
        score[score >= 0.5] = 1.
        score[score < 0.5] = 0.
        score = score.view(label.size())
        # print(score==label)
        acc = (score == label).float().mean()
        self.acc += acc.item()
        self.iter_number += 1
        return loss.item(), self.acc / self.iter_number

    def train_on_batch_triplet(self, query, p_response, n_response, alpha=10):
        query = torch.tensor(query).long()
        p_response = torch.tensor(p_response).long()
        n_response = torch.tensor(n_response).long()
        # label = torch.tensor(label).float()
        ################## train
        self.match_net.train()
        p_output = self.match_net.forward(query, p_response)
        n_output = self.match_net.forward(query, n_response)
        # 距离越小越相关
        triplet_loss = self.hingle_loss(p_output - n_output + alpha)
        self.opt.zero_grad()
        triplet_loss.backward()
        self.opt.step()
        #################### test
        self.match_net.eval()
        with torch.no_grad():
            p_output = self.match_net.forward(query, p_response)
            n_output = self.match_net.forward(query, n_response)
        score = (p_output < n_output).float()
        # print(score==label)
        acc = score.mean()
        self.acc += acc.item()
        self.iter_number += 1
        return triplet_loss.item(), self.acc / self.iter_number

    def get_score(self, query, response):
        query = torch.tensor(query).long()
        response = torch.tensor(response).long()
        self.match_net.eval()
        with torch.no_grad():
            score = self.match_net.forward(query, response)
            score = torch.sigmoid(score)
        return score.item()

    def save(self, path):
        path = os.path.join(path, "matcher.pth")
        torch.save(self.match_net.state_dict(), path)

    def load(self, path):
        path = os.path.join(path, "matcher.pth")
        self.match_net.load_state_dict(torch.load(path))
