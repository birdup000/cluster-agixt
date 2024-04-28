from typing import Callable, Dict, List, Any
from agixtsdk import AGiXTSDK
import math
import time

class ClusterCoordinator:
    def __init__(self, base_uri: str, api_key: str, nodes: List[str]):
        self.sdk = AGiXTSDK(base_uri=base_uri, api_key=api_key)
        self.nodes = nodes
        self.task_execution_agents = {node: self.sdk.add_agent(f"agent_{node}") for node in nodes}
        self.subtask_assignments = {}

    def decompose_task(self, task: Callable, *args, **kwargs) -> List[Dict[str, Any]]:
        # Analyze the task and break it down into smaller, parallelizable subtasks
        subtasks = []
        num_subtasks = len(self.nodes)
        
        # Example decomposition: Split the input data into smaller chunks
        data = args[0]
        chunk_size = math.ceil(len(data) / num_subtasks)
        for i in range(num_subtasks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(data))
            subtasks.append({
                "task": task,
                "args": (data[start:end],),
                "kwargs": kwargs
            })
        
        return subtasks

    def assign_subtasks(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        # Assign the subtasks to the available nodes in the cluster
        self.subtask_assignments = {node: [] for node in self.nodes}
        
        # Example assignment: Round-robin assignment of subtasks to nodes
        for i, subtask in enumerate(subtasks):
            node = self.nodes[i % len(self.nodes)]
            self.subtask_assignments[node].append(subtask)
        
        return self.subtask_assignments

    def aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Combine the results from the executed subtasks
        final_result = {"result": sum(result["result"] for result in results)}
        return final_result

    def execute_task(self, task: Callable, *args, **kwargs) -> Dict[str, Any]:
        # Decompose the task into subtasks
        subtasks = self.decompose_task(task, *args, **kwargs)

        # Assign the subtasks to the nodes
        self.assign_subtasks(subtasks)

        # Execute the subtasks in parallel
        results = []
        for node, node_subtasks in self.subtask_assignments.items():
            agent = self.task_execution_agents[node]
            for subtask in node_subtasks:
                result = self.sdk.prompt_agent(
                    agent_name=agent["agent_name"],
                    prompt_name="execute_subtask",
                    prompt_args=subtask,
                )
                results.append(result)

        # Aggregate the results
        final_result = self.aggregate_results(results)
        return final_result