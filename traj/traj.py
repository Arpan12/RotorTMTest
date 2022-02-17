#! /usr/bin/env python


from generate_poly import generate_poly
from numpy import sin
from numpy import cos
import numpy as np


class traj:
	def __init__(self):
		# for circles
		self.Radius = None
		self.ramp_theta_coeff = None
		self.zcoeff = None
		self.tf = None
		self.offset_pos = None
		self.T = None 
		self.omega_des = None
		self.ramp_t = None
		self.ramp_dist = None
		self.circle_dist = None
		self.start = None
		self.duration = None

		# for line_quintic_traj_generator
		self.mapquad = None
		self.pathall = None
		self.coefficient = None
		self.finalpath = None
		self.timepoint = None
		self.timesegment = None

		# for min_snap_traj_generator
		self.snap_coeff = None
		self.snap_finalpath = None
		self.timelist = None
		self.polynomial_coeff = None
		self.traj_constant = None

	def circle(self, t, state_struct, init_pos = None, r = None, period = None, circle_duration = None):
		# CIRCLE trajectory generator for a circle

		# =================== Your code goes here ===================
		# You have to set the pos, vel, acc, yaw and yawdot variables
		

		if (np.all(init_pos!=None)) and (r != None) and (period != None) and (circle_duration != None):
			print('Generating Circular Trajectory ...')
			self.Radius = r
			offset_pos_temp = np.append(init_pos[0]-self.Radius, init_pos[1], axis=0)
			self.offset_pos = np.append(offset_pos_temp, np.array([0]))
			self.T = period
			self.omega_des = 2*np.pi/self.T
			self.alpha_des = np.pi/40
			self.start = init_pos
			self.ramp_t = self.omega_des/self.alpha_des
			self.duration = circle_duration

			thetainitial = np.array([[0],[0],[0],[self.ramp_t*self.omega_des],[0],[0]])
			A = np.append(generate_poly(5,2,0), generate_poly(5,2,1), axis = 0)

			self.ramp_theta_coeff = np.matmul(np.linalg.inv(A), thetainitial)
			self.ramp_dist = sum(np.multiply(self.ramp_theta_coeff, np.array([[1],[1/2],[1/3],[1/4],[1/5],[1/6]])))
			self.circle_dist = self.omega_des*self.duration
			self.tf = self.ramp_t * 2 + self.duration
			final_theta = 2 * self.ramp_dist + self.circle_dist
			x_pos = self.Radius * np.cos(final_theta)
			y_pos = self.Radius * np.sin(final_theta)
			stop_pos_temp = np.append(x_pos, y_pos, axis=0)
			stop_pos_temp = np.append(stop_pos_temp, self.start[2], axis=0)
			stop = np.add(self.offset_pos, stop_pos_temp)
		else:
			if t < self.tf:
				if t<=self.ramp_t:  # ramping up the circle
					dt = t/self.ramp_t
					integral_poly = generate_poly(6,0,dt)
					integral_poly = np.multiply(integral_poly[:,1:7],[1,1/2,1/3,1/4,1/5,1/6])
					polynominalmat = np.append(integral_poly, generate_poly(5,2,dt), axis=0)
					theta_d = np.matmul(polynominalmat, self.ramp_theta_coeff)
					theta_d = np.multiply(theta_d, np.array([[1],[1/self.ramp_t],[1/self.ramp_t**2],[1/self.ramp_t**3]]))
				else:
					if t<=(self.ramp_t + self.duration): # constant velocity cruising
						dt = t - self.ramp_t
						theta_d = np.zeros((4,1),dtype=float)
						theta_d[0] = self.omega_des * dt + self.ramp_dist
						theta_d[1] = self.omega_des

					else:  # ramping down the circle
						dt = 1 - (t - self.duration - self.ramp_t)/self.ramp_t
						integral_poly = generate_poly(6,0,dt)
						integral_poly = np.multiply(integral_poly[:,1:7],[1,1/2,1/3,1/4,1/5,1/6])
						polynominalmat = np.append(integral_poly, generate_poly(5,2,dt), axis=0)

						theta_d = np.matmul(polynominalmat, self.ramp_theta_coeff)
						theta_d = np.multiply(theta_d, np.array([[1],[1/self.ramp_t],[1/self.ramp_t**2],[1/self.ramp_t**3]]))
						theta_d[0] = self.circle_dist + 2*self.ramp_dist - theta_d[0]

				x_pos = self.Radius * cos(theta_d[0])
				y_pos = self.Radius * sin(theta_d[0])
				x_vel = -self.Radius * sin(theta_d[0]) * theta_d[1]
				y_vel =  self.Radius * cos(theta_d[0]) * theta_d[1]
				x_acc = -self.Radius * cos(theta_d[0]) * theta_d[1]**2 - self.Radius * sin(theta_d[0]) * theta_d[2]
				y_acc = -self.Radius * sin(theta_d[0]) * theta_d[1]**2 + self.Radius * cos(theta_d[0]) * theta_d[2]
				x_jrk = self.Radius * sin(theta_d[0]) * theta_d[1]**3 - 3 * self.Radius * cos(theta_d[0]) * theta_d[1] * theta_d[2] - self.Radius * sin(theta_d[0]) * theta_d[3]
				y_jrk = -self.Radius * cos(theta_d[0]) * theta_d[1]**3 - 3 * self.Radius * sin(theta_d[0]) * theta_d[1] * theta_d[2] + self.Radius * cos(theta_d[0]) * theta_d[3]

				temp_pos = np.append(x_pos, y_pos, axis=0)
				temp_pos = np.append(temp_pos, self.start[2], axis=0)
				pos = np.add(self.offset_pos, temp_pos)
				last_pos = pos
				vel = np.append(x_vel, y_vel, axis=0)
				vel = np.append(vel, np.array([0.0]), axis=0)
				acc = np.append(x_acc, y_acc, axis=0)
				acc = np.append(acc, np.array([0.0]), axis=0)
				jrk = np.append(x_jrk, y_jrk, axis=0)
				jrk = np.append(jrk, np.array([0.0]), axis=0)
				yaw = 0
				yawdot = 0
			else:
				pos = self.last_pos
				vel = np.array([[0],[0],[0]])
				acc = np.array([[0],[0],[0]])
				jrk = np.array([[0],[0],[0]])
				yaw = 0
				yawdot = 0

			state_struct["pos_des"] = pos
			state_struct["vel_des"] = vel
			state_struct["acc_des"] = acc
			state_struct["jrk_des"] = jrk
			state_struct["qd_yaw_des"] = yaw
			state_struct["qd_yawdot_des"] = yawdot
			state_struct["quat_des"] = np.array([1,0,0,0])
			state_struct["omega_des"] = np.array([0,0,0])
			return state_struct

	def line_quintic_traj(self, t, map = None, path = None):

		# map is a class 
		# path is a 2D array
		desired_state = {}
		if (np.any(map!= None) ) and (np.any(path != None)):
			self.mapquad = map
			self.pathall = path
			pathqn = self.pathall # ####may need modification
			ttotal = 10

			xy_res = map.resolution[0]
			basicdata = map.basicdata
			rowbasicdata = basicdata.shape[0]
			if rowbasicdata >= 2: # might need to be changed to 1
				block = basicdata[1:rowbasicdata,:]
			else:
				block = np.array([])

			# finalpath = simplify_path(pathqn,block,mapquad)
			# use pathqn as the final path
			self.finalpath = pathqn

			pathlength = self.finalpath.shape[0]
			m = pathlength - 1

			distance = np.zeros((self.finalpath.shape[0],1))
			self.timesegment = np.zeros((self.finalpath.shape[0], 2))

			for i in range(1, m+1):
				previous = self.finalpath[i-1, :]
				afterward = self.finalpath[i, :]

				distance[i-1, :] = np.linalg.norm(afterward-previous)
				if distance[i-1,:]<=1:
					self.timesegment[i-1, 0] = distance[i-1,:]
					self.timesegment[i-1, 1] = 0 # change back to 1 when done
				else:
					self.timesegment[i-1, :] = np.sqrt(distance[i-1,:])*2
					self.timesegment[i-1, 1] = 0
			
			time_temp = 0
			self.timepoint = np.zeros((m, 1))
			for i in range(1, m+1):
				time_temp = time_temp + self.timesegment[i-1, 0]
				self.timepoint[i-1, 0] = time_temp
			self.timepoint = np.append(np.array([[0]]), self.timepoint, axis = 0)

			constraints = np.zeros((6*m, 6), dtype=float)
			condition = np.zeros((6*m, 3), dtype=float)
			self.coefficient = np.zeros((6*m, 3), dtype=float)
			for j in range(1, m+1):
				tstart = 0
				tend = self.timesegment[j-1, 0]

				constraints[6*j-6,:] = np.array([1, tstart, tstart**2, tstart**3  ,   tstart**4   ,  tstart**5])
				constraints[6*j-5,:] = np.array([0, 1     , 2*tstart, 3*tstart**2,   4*tstart**3 ,  5*tstart**4])
				constraints[6*j-4,:] = np.array([0, 0     , 2       , 6*tstart  ,   12*tstart**2,  20*tstart**3])
				constraints[6*j-3,:] = np.array([1, tend  , tend**2  , tend**3    ,   tend**4     ,  tend**5     ])
				constraints[6*j-2,:] = np.array([0, 1     , 2*tend  , 3*tend**2  ,   4*tend**3   ,  5*tend**4   ])
				constraints[6*j-1,:] = np.array([0, 0     , 2       , 6*tend    ,   12*tend**2  ,  20*tend**3  ])
				condition  [6*j-6,:] = self.finalpath[j-1,:]
				condition  [6*j-3,:] = self.finalpath[j,:]
				inverse = np.linalg.inv(constraints[6*j-6:6*j,0:6])
				coefficient_temp = np.matmul(inverse,condition[6*j-6:6*j,0:3])
				self.coefficient[6*j-6:6*j,0:3] = coefficient_temp

		else:
				lengthtime = self.timepoint.shape[0]
				length = lengthtime -1 
				desired_state["yaw"] = 0
				desired_state["yawdot"] = 0
				state = np.zeros((3, 3), dtype=float)
				for i in range(1, length+1):
					if (t >= self.timepoint[i-1][0]) and (t < self.timepoint[i][0]) and (self.timesegment[i-1, 1] == 0):
						currenttstart = self.timepoint[i-1][0]
						state = np.array([[1, (t-currenttstart), (t-currenttstart)**2, (t-currenttstart)**3, (t-currenttstart)**4, (t-currenttstart)**5], [0, 1, 2*(t-currenttstart), 3*(t-currenttstart)**2, 4*(t-currenttstart)**3, 5*(t-currenttstart)**4], [0, 0, 2, 6*(t-currenttstart), 12*(t-currenttstart)**2, 20*(t-currenttstart)**3]]) 
						state = np.matmul(state, self.coefficient[6*i-6:6*i,0:3])
					elif (t >= self.timepoint[i-1]) and (t < self.timepoint[i]) and (self.timesegment[i-1, 1] == 1):
						state[0, :] = self.finalpath[i,:]
						state[1, :] = np.array([0,0,0])
						state[2, :] = np.array([0,0,0])
					elif (t >= self.timepoint[lengthtime-1]):
						state[0, :] = self.finalpath[lengthtime - 1, :]
						state[1, :] = np.array([0,0,0])
						state[2, :] = np.array([0,0,0])
				desired_state["pos"] = np.transpose(state[0,:])
				desired_state["vel"] = np.transpose(state[1,:])
				desired_state["acc"] = np.transpose(state[2,:])
				return desired_state
