from mobile import block

block1 = block.TxBlock(1, 1, None)
block2 = block.TxBlock(1, 2, None)
block3 = block.TxBlock(1, 3, None)

list1 = []
list1.append(block2)
list1.append(block1)
list1.append(block3)

list_ = sorted(list1, key=lambda x: x.shard_length)
print(list1[0].shard_length)
print(list_[0].shard_length)
