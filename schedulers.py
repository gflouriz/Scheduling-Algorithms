import numbers
from enum import Enum, auto

from des import SchedulerDES
from event import Event, EventTypes
from process import Process, ProcessStates


class FCFS(SchedulerDES):
    def scheduler_func(self, cur_event):
        """
        
        :param cur_event: 
        Iterate through the processes to find the one that matches the event's ID
        :return: 
        """
        for cur_process in self.processes:
            if cur_event.process_id == cur_process.process_id:
                return cur_process

    def dispatcher_func(self, cur_process):
        """
        
        :param cur_process: 
        Set the process' state to running,run it to completion,
        set it to terminated,return a new event signaling that cpu is done
        
        :return: 
        """
        cur_process.process_state = ProcessStates.RUNNING
        time_to_completion = cur_process.service_time
        cur_process.run_for(time_to_completion, self.time)
        cur_process.process_state = ProcessStates.TERMINATED
        new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_DONE,
                          event_time=cur_process.departure_time)
        return new_event


class SJF(SchedulerDES):
    def scheduler_func(self, cur_event):
        """

        :param cur_event:
        Iterates through the processes,looks if the Processes are Ready
        Define the minimum as the first ready object and then if the next ready object
        is less than the defined minimum redefine the minimum as the next object while
        keeping the position of the minimum process in a variable

        :return the minimum process:
        """
        ready_process = [i for i in self.processes if i.process_state == ProcessStates.READY]
        first_ready_process = True
        for i, selected_process in enumerate(self.processes):
            if selected_process.process_state == ProcessStates.READY:
                if first_ready_process:
                    first_ready_process = False
                    minim = selected_process.service_time
                    i_min = i
                elif minim > selected_process.service_time:
                    minim = selected_process.service_time
                    i_min = i

        cur_process = self.processes[i_min]
        return cur_process

    def dispatcher_func(self, cur_process):
        """
        
        :param cur_process: 
        Set the process' state to running,run it to completion,
    set it to terminated,return a new event signaling that cpu is done
        :return: 
        """
        cur_process.process_state = ProcessStates.RUNNING
        time_to_completion = cur_process.service_time
        cur_process.run_for(time_to_completion, self.time)
        cur_process.process_state = ProcessStates.TERMINATED
        new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_DONE,
                          event_time=cur_process.departure_time)
        return new_event


class RR(SchedulerDES):
    def scheduler_func(self, cur_event):
        """
        :param cur_event:
        Take the latest process and run it
        :return:
        """
        for cur_process in self.processes:
            if cur_event.process_id == cur_process.process_id:
                return cur_process

    def dispatcher_func(self, cur_process):
        """

        :param cur_process:
        Set the process' state to running,run it for a maximum time of "quantum" or until completion,
        whichever comes first).If the process that was ran is done,then make its state
        Terminated,otherwise make its state Ready and put it to the end of the queue

        :return the event that signals either the termination of the process or the queueing of the process:
        """
        cur_process.process_state = ProcessStates.RUNNING
        time_to_completion = cur_process.remaining_time

        if time_to_completion <= self.quantum:
            cur_process.run_for(time_to_completion, self.time)
            cur_process.process_state = ProcessStates.TERMINATED
            new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_DONE,
                              event_time=cur_process.departure_time)
        else:
            cur_process.run_for(self.quantum, self.time)
            cur_process.process_state = ProcessStates.READY
            new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_REQ,
                              event_time=self.time + self.quantum)

        return new_event


class SRTF(SchedulerDES):
    def scheduler_func(self, cur_event):
        """

        :param cur_event:
        Iterates through the processes,looks if the Processes are Ready
        Checks if the process is on the CPU and adds context switch time if it's not
        Define the minimum as the first ready object and then if the next ready object
        is less than the defined minimum redefine the minimum as the next object while
        keeping the position of the minimum process in a variable

        :return the minimum process:
        """
        first_ready_process = True
        for i, selected_process in enumerate(self.processes):
            if selected_process.process_state == ProcessStates.READY:
                if self.process_on_cpu != selected_process:
                    selected_process_time_left=selected_process.remaining_time+self.context_switch_time
                else:
                    selected_process_time_left=selected_process.remaining_time
                if first_ready_process:
                    first_ready_process = False
                    minim = selected_process_time_left
                    i_min = i
                elif minim > selected_process_time_left:
                    minim = selected_process_time_left
                    i_min = i

        cur_process = self.processes[i_min]
        return cur_process

    def dispatcher_func(self, cur_process):
        """

        :param cur_process:
        Set the process' state to running,run it until the next event occurs or until completion,
        whichever comes first.If the process that was ran is done,then make its state
        Terminated,otherwise make its state Ready and put it back on the queue

        :return the event that signals either the termination of the process or the queueing of the process:
        """
        cur_process.process_state = ProcessStates.RUNNING
        time_to_completion = cur_process.remaining_time
        next_event = self.next_event_time()
        time_now = self.time
        # If calculated time of completion is sooner or equal to next event's time of arrival
        if next_event >= time_to_completion + time_now:
            cur_process.run_for(time_to_completion, time_now)
            cur_process.process_state = ProcessStates.TERMINATED
            new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_DONE,
                              event_time=cur_process.departure_time)
        else:

            cur_process.run_for(next_event - time_now, time_now)
            cur_process.process_state = ProcessStates.READY
            new_event = Event(process_id=cur_process.process_id, event_type=EventTypes.PROC_CPU_REQ,
                              event_time=next_event)

        return new_event
