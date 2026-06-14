import { useQuery } from '@tanstack/react-query'
import { getImpact } from '../services/api'

export function useImpact(autoRefresh: boolean = true) {
  return useQuery({
    queryKey: ['impact'],
    queryFn: getImpact,
    refetchInterval: autoRefresh ? 5_000 : false,
  })
}