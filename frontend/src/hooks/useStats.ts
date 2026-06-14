import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getStats, clearCache } from '../services/api'

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    refetchInterval: 15_000,
  })
}

export function useClearCache() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: clearCache,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['stats'] })
      qc.invalidateQueries({ queryKey: ['impact'] })
    },
  })
}
