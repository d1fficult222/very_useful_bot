"""
Key: 
- 使用堆来模拟西瓜的堆积
- 每次吃一个西瓜时，从堆顶开始计数，直到找到目标西瓜
"""

# 輸入
n = int(input())
a = list(map(int, input().replace('.',' ').split()))
b = list(map(int, input().replace('.',' ').split()))

# 当前的堆
stack = a[:]

result = []
for i in range(n):
    target = b[i]
    if target in stack:
        # 找到目标的位置
        pos = stack.index(target)
        # 需要吃的数量（包括目标西瓜本身）
        count = pos + 1
        result.append(count)
        # 移除这些西瓜（从栈顶到目标西瓜）
        stack = stack[pos+1:]
    else:
        # 已经被吃过了
        result.append(0)

# 输出结果
print(' '.join(map(str, result)))