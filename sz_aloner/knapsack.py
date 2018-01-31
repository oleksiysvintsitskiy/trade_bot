def knapsack(W, price, prof, n):
	K = [[0 for x in range(W+1)] for x in range(n+1)]

	for i in range(n+1):
		for w in range(W+1):
			if i==0 or w==0:
				K[i][w] = 0
			elif price[i-1] <= w:
				K[i][w] = max(prof[i-1] + K[i-1][w-price[i-1]],  K[i-1][w])
			else:
				K[i][w] = K[i-1][w]

	res_deal = []
	def findans(i, j):
		if K[i][j] == 0:
			return
		if K[i-1][j] == K[i][j]:
			findans(i-1, j)
		else:
			findans(i-1, j-price[i-1])
			res_deal.append(i-1)

	findans(n, W)

	return K[n][W], res_deal